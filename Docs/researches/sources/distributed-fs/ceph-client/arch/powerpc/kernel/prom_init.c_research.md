# sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_init.c

## Purpose
`prom_init.c` is the early PowerPC Open Firmware bridge that runs before the normal kernel mapping and runtime services are available. Its job is to talk to the firmware while firmware calls are still safe, discover boot-time platform state, claim and reserve early memory, instantiate RTAS/SML/TCE resources, fix known firmware device-tree defects, flatten the Open Firmware tree into the boot parameter format, quiesce firmware, and tail-call `__start()` with the flattened device tree and kernel base.

## Important APIs, Types, And Functions
Key local types are `struct prom_args` for 32-bit OF client-interface calls, `struct prom_t` for handles to `/chosen`, root, stdout, MMU, and memory packages, `struct mem_map_entry` for the reserve map copied into the flattened tree, and pSeries option-vector structures used by `ibm,client-architecture-support`. `call_prom()` and `call_prom_ret()` are the central firmware-call gateways; all OF services go through them and `enter_prom()`. `prom_init()` is the only exported entry in this file and orchestrates the complete handoff. Other important helpers include `early_cmdline_parse()`, `prom_send_capabilities()`, `prom_init_mem()`, `alloc_up()`, `alloc_down()`, `prom_instantiate_rtas()`, `prom_initialize_tce_table()`, `prom_hold_cpus()`, `fixup_device_tree()`, and `flatten_device_tree()`.

## Control Flow
`prom_init()` first relocates 32-bit GOT state if needed, clears BSS, initializes OF service handles, applies old-firmware MMU workarounds, opens stdout, identifies the platform, checks initrd arguments, parses boot options, and optionally sends pSeries capability vectors. It then copies the low-memory secondary CPU holding code, scans memory nodes to configure the early allocator, finds the boot CPU, opens displays, creates pSeries TCE tables, instantiates RTAS and SML, holds secondary CPUs, publishes selected boot properties under `/chosen`, applies device-tree fixups, flattens the tree, closes stdin on non-PowerMac systems, calls `quiesce`, optionally enters secure guest mode, and finally calls `__start(hdr, kbase, 0, ...)`.

## State And Persistence
The file relies on `.bss.prominit` globals because ordinary kernel services are not live. Persistent boot state written for the later kernel includes `/chosen/linux,stdout-path`, initrd start/end, memory limit, IOMMU flags, TCE allocation bounds, RTAS base/entry, SML base/size, `linux,boot-display`, and the flattened device-tree reserve map. Allocator state is held in `alloc_bottom`, `alloc_top`, `alloc_top_high`, `rmo_top`, and `ram_top`; reserve state is bounded by `MEM_RESERVE_MAP_SIZE`.

## Dependencies And Integration Points
This code integrates with Open Firmware client services, pSeries PAPR capability negotiation, platform-specific device-tree quirks, low-level relocation helpers, secondary CPU holding code, RTAS, SML/vTPM firmware methods, IOMMU/TCE firmware calls, the flattened device-tree format, and secure virtual machine ultravisor calls. It deliberately avoids normal kernel library dependencies and uses local string/parse/print helpers to avoid relocation and external-symbol hazards.

## Risks
The riskiest areas are external symbol creep, firmware calls after mappings become unsafe, allocator overlap with kernel/initrd/TCE/RTAS/device-tree memory, incomplete reserve-map accounting, bad endian or cell-size handling while scanning memory and device-tree properties, and stale platform workarounds. Device-tree fixups mutate firmware state by path and can be brittle if firmware layouts vary. Secure guest setup temporarily relocates the kernel back and forth around the ultracall, so relocation correctness is critical.

## Test Signals
Strong build-time signals include `prom_init_check.sh`, link success under PPC32/PPC64 and BE/LE configurations, and `BUILD_BUG_ON`/configuration coverage in dependent assembly and headers. Runtime signals include early console output, correct `/chosen` properties, successful RTAS/SML/TCE reservations, stable secondary CPU bring-up, boot with `mem=`, `iommu=`, `disable_radix`, `xive=off`, and `svm=` options, and successful boot on pSeries, PowerMac, CHRP/Pegasos, Efika, and PA-Semi/Nemo firmware variants.
