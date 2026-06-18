<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_lpi_stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_lpi_stress.c

Purpose: this test stresses KVM's emulated GICv3 ITS/LPI path by configuring ITS device/event mappings in the guest, then concurrently signaling many LPIs from host threads while vCPU threads consume them.

Important APIs, types, and functions: `struct test_data` records CPU, device, event counts and guest physical addresses for ITS tables, command queue, ITTs, LPI property table, and pending tables. Guest setup uses `gic_init()`, `gic_rdist_enable_lpis()`, `its_init()`, `its_send_mapc_cmd()`, `its_send_mapd_cmd()`, `its_send_mapti_cmd()`, `its_send_invall_cmd()`, and `its_send_sync_cmd()`. Host setup uses `vgic_its_setup()`, `vm_userspace_mem_region_add()`, `vm_phy_pages_alloc()`, and `virt_map()`. `signal_lpi()` sends `KVM_SIGNAL_MSI` with `KVM_MSI_VALID_DEVID`.

Control flow: `main()` parses `-v`, `-d`, `-e`, and `-i`, warns if thread count exceeds online CPUs, creates the VM/vCPUs, installs an IRQ handler, allocates a high GPA memslot for ITS/LPI tables, sets up the ITS, syncs `test_data` to the guest, and starts the stress run. Each vCPU reaches guest setup then syncs at a barrier. Each device has a host LPI worker that signals all event IDs for the configured iteration count. After LPI workers finish, the host writes `request_vcpus_stop` in guest memory and joins vCPUs.

State, persistence, and dependencies: state is transient VM memory plus host pthread synchronization. Guest table memory is allocated in a dedicated memslot and identity mapped for the command queue. Dependencies include VGICv3 and ITS support, `KVM_SIGNAL_MSI`, GICv3 ITS helper library, pthread barriers, atomics, and enough host CPUs for reliable performance.

Risks and edge cases: table sizing assumes 64 KiB units and one ITT per device. The test intentionally avoids WFI in the guest loop after setup so stop signaling cannot hang indefinitely. Concurrent MSI signaling stresses translation, injection, and LPI handling but does not count every delivered LPI in guest state, so it is more of a crash/performance stressor than an exact delivery accounting test.

Test signals: guest IRQ handler asserts every handled intid is an LPI (`>= 8192`). `KVM_SIGNAL_MSI` must return 1 for translated, unblocked MSIs. Completion prints an LPI/sec rate. Missing VGICv3 support skips the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_lpi_stress.c -->
