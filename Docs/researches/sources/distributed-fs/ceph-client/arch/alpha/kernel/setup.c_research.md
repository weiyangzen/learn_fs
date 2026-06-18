# sources/distributed-fs/ceph-client/arch/alpha/kernel/setup.c

## Purpose
`setup.c` is the central Alpha architecture boot setup file. It parses firmware/HWRPB state and command-line overrides, selects the `alpha_machine_vector`, initializes SRM callbacks, memory, HAE, resources, machine architecture hooks, console defaults, SMP discovery, paging, CPU cache descriptors, `/proc/cpuinfo`, panic handling, and a PC speaker platform device.

## Important APIs, Types, And Functions
- Global boot state includes `hwrpb`, `srm_hae`, cache shape globals, `alpha_verbose_mcheck`, `boot_cpuid`, `srmcons_output`, `mem_size_limit`, `alpha_agpgart_size`, `alpha_mv`, `alpha_using_srm`, `alpha_using_qemu`, `__direct_map_base`, and `__direct_map_size`.
- Weak machine vector declarations allow generic kernels to reference many board vectors.
- `reserve_std_resources()` reserves legacy PC-compatible I/O regions under the first hose or global I/O resource.
- `get_mem_size_limit()` parses `mem=` and `gartsize=` units.
- `move_initrd()` relocates initrd below the memory limit when needed.
- `setup_memory()` reads HWRPB memory clusters, adds/reserves memblock ranges, applies memory limits, reserves kernel/initrd memory, and sets `max_low_pfn`.
- `page_is_ram()` checks if a PFN belongs to a non-reserved HWRPB memory cluster.
- `register_cpus()` creates CPU devices for possible CPUs.
- `setup_arch()` is the boot entry point for most architecture setup.
- `get_sysvec()`, `get_sysvec_byname()`, and `get_sysnames()` map HWRPB type/variation/CPU to machine vectors and printable names.
- `platform_string()`, `show_cpuinfo()`, and `cpuinfo_op` back `/proc/cpuinfo`.
- `determine_cpu_caches()` and `external_cache_probe()` populate cache shape data.
- `alpha_panic_event()` hard-halts certain SRM console panic paths.
- `add_pcspkr()` registers `pcspkr`.

## Control Flow
`setup_arch()` starts by locating the HWRPB, capturing boot CPU ID, normalizing negative system types, registering the panic notifier, detecting SRM/MILO and QEMU, initializing SRM callbacks, and parsing command-line options such as `alpha_mv=`, `cycle=`, `mem=`, `srmcons`, `console=srm`, `gartsize=`, and `verbose_mcheck=`.

It then optionally registers SRM console output, adjusts SysRq reboot behavior under SRM, derives system names, selects a machine vector by command line or HWRPB, copies it into `alpha_mv`, logs boot options, saves/restores HAE state, enables machine checks, sets up memory, probes cache sizes, calls `alpha_mv.init_arch()`, reserves legacy I/O resources, registers VGA screen info, sets default root to `sda2`, enables EISA when configured, validates ASN, discovers SMP CPUs, and finally calls `paging_init()`.

Machine vector selection first tries fixed system tables and API/unofficial tables, then variation-specific member IDs for Alcor, EB164, Marvel, Titan, Tsunami, and several legacy platforms. Name lookup allows command-line override against a list of known vectors.

## State And Persistence
This file establishes long-lived architecture globals and boot memory state. It mutates HWRPB checksum/state for system type normalization, stores SRM HAE, sets memblock regions, root device, cache shape globals, selected machine vector, CPU masks via `setup_smp()`, and registered CPU/platform devices. No disk persistence exists; firmware-provided HWRPB data is the persistent input.

## Dependencies And Integration Points
`setup.c` integrates with Alpha firmware/HWRPB, SRM callbacks, machine vectors from many `sys_*.c` files, host bridge init, memblock, initrd, VGA/VT console, EISA, SMP, paging, panic notifiers, sysrq, `/proc/cpuinfo`, and platform devices. Other files consume globals declared here through `proto.h`.

## Risks
- Machine-vector selection is table-heavy and depends on HWRPB type/variation quirks; wrong vector selection breaks interrupts, PCI, memory windows, and shutdown.
- Memory cluster handling reserves only usage bits 0/1 and enforces a default 32 GiB cap for non-discontiguous NUMA cases.
- External cache probing reads physical address zero with timing loops; it assumes safe early boot conditions.
- Command-line parsing uses destructive `strsep()` and restores from `boot_command_line`; future edits must preserve command-line lifetime.
- `alpha_panic_event()` hard-halts under SRM serial console, bypassing ordinary panic progression.

## Test Signals
- Boot logs identify correct system type, variation, machine vector, SRM/MILO source, HAE, memory clusters, cache sizes, and options.
- `mem=`, `gartsize=`, `cycle=`, `alpha_mv=`, `srmcons`, and `console=srm` command-line options behave as expected.
- `/proc/cpuinfo` reports CPU, system, cache, unaligned access, and SMP fields.
- Supported board configs boot through `alpha_mv.init_arch/init_irq/init_pci`.
- Initrd relocation works when initrd lies above memory limit.
