# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_topology.c

## Purpose
Maintains KFD's HSA topology model and exports it through sysfs. It creates a CPU topology node from virtual CRAT data during init, adds/removes GPU nodes as KFD devices appear and disappear, synthesizes cache/memory/I/O/P2P details not present in CRAT, assigns stable-ish GPU ids, exposes node properties under `/sys/class/kfd/kfd/topology`, and updates capability bits such as SVM, debug, RAS, doorbells, atomics, and coherent host access.

## Important APIs, Types, And Functions
Global state includes `topology_device_list`, `sys_props`, `topology_lock`, and `topology_crat_proximity_domain`. Lookup helpers include `kfd_topology_device_by_proximity_domain`, `kfd_topology_device_by_id`, and `kfd_device_by_id`. Lifecycle entry points are `kfd_topology_init`, `kfd_topology_shutdown`, `kfd_topology_add_device`, and `kfd_topology_remove_device`. Sysfs show/build/remove paths are implemented by `sysprops_show`, `node_show`, `mem_show`, `kfd_cache_show`, `iolink_show`, `perf_show`, `kfd_build_sysfs_node_entry`, and `kfd_topology_update_sysfs`. GPU enrichment is handled by `kfd_generate_gpu_id`, `kfd_fill_cache_non_crat_info`, `kfd_fill_iolink_non_crat_info`, `kfd_dev_create_p2p_links`, `kfd_topology_set_capabilities`, and `kfd_update_svm_support_properties`.

## Control Flow
Initialization creates and parses a CPU VCRAT, moves parsed devices into the master list under the write lock, builds sysfs, increments `generation_count`, and patches CPU memory data from DMI. Adding a GPU first tries to attach it to a parsed GPU topology entry; otherwise it creates/parses a GPU VCRAT, moves the result to the master list, assigns the `kfd_node`, fills cache data, rebuilds sysfs, then assigns a GPU id and fills non-CRAT properties such as public name, clocks, render minor, SDMA counts, RAS/SVM/debug capabilities, memory clock, I/O link flags, and P2P links. Removal deletes the sysfs node, frees the topology device, decrements device counts, renumbers proximity domains and links, rebuilds sysfs, and sends a placeholder change notification.

## State And Persistence
Topology is in-memory kernel state rebuilt from VCRAT/CRAT, PCI/amdgpu device data, DMI, and runtime partition data. `sys_props.generation_count` changes on accepted topology/sysfs updates. `gpu_id` is generated from PCI identity, local memory size, and XCC mask with collision avoidance against the current live list; it is stable for a given boot/device view but not a persistent registry.

## Dependencies And Integration Points
Uses KFD CRAT parsing/creation, KFD queue manager/debug helpers, SVM support macro, amdgpu device, RAS, XGMI, PCIe capability reads, DMI, sysfs/kobject APIs, cpufreq, devcgroup permission checks, optional P2P configuration, and debugfs hooks for HQD/runlist dumps. It is consumed by userspace ROCm/HSA tooling through sysfs and by in-kernel KFD lookups by GPU id or proximity domain.

## Risks
Sysfs rebuilds are all-or-partial operations; error paths can leave sysfs partially constructed until later release/rebuild. The topology list is protected by an rwsem, but sysfs show functions read object fields that can change across device add/remove and rely on object lifetime through kobjects. GPU id hashing is collision-handled but not globally stable. P2P and indirect-link synthesis has many topology assumptions around CPU nodes, large BAR, XGMI hives, and peer accessibility. Capability bits depend on firmware version tables, so new ASICs require careful updates.

## Test Signals
Signals include boot topology sysfs presence, generation counter increments on GPU add/remove and SVM support update, correct node counts and proximity-domain renumbering after hot unplug, devcgroup permission denial in show paths, P2P link creation for PCIe and XGMI systems, cache sibling maps across XCC partitions, render minor correctness for XCP partitions, debug capability bits across firmware versions, and debugfs HQD/runlist enumeration.
