# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x.h

## Purpose
This header is the main ETMv4/ETE register and data-contract definition file for CoreSight instruction trace sources. It defines trace register offsets, field masks, sysreg access tables, MMIO/sysreg read/write wrappers, supported resource limits, mode bits, architecture identity helpers, and the driver-private configuration/save-state structures used by the ETM4 driver implementation.

## Important APIs, Types, And Functions
Important macros include `TRC*` register offsets, `TRCIDR*` capability masks, `TRCCONFIGR_*`, `TRCVICTLR_*`, address-comparator masks, resource selector helpers, and ETM mode bits such as `ETMv4_MODE_TIMESTAMP`, `ETM_MODE_EXCL_KERN`, and `ETM_MODE_EXCL_USER`. `etm4_res_sel_single()` and `etm4_res_sel_pair()` validate and encode event resource selectors, warning on invalid selector widths and rejecting pair selector zero. The `ETM_COMMON_SYSREG_LIST`, `ETM4x_ONLY_SYSREG_LIST`, `ETE_ONLY_SYSREG_LIST`, and `ETM_MMAP_LIST` macro lists are central to selecting whether an offset may be accessed through system registers or only through MMIO. `etm4x_relaxed_read32/64`, `etm4x_read32/64`, and matching write macros abstract over `struct csdev_access` choosing `base` MMIO when `io_mem` is true or `etm4x_sysreg_read/write()` otherwise. The main types are `struct etmv4_config`, `struct etmv4_save_state`, and `struct etmv4_drvdata`.

## Control Flow And State
This file is declarative, but it drives runtime control flow in the ETM driver. Probe code fills `struct etmv4_drvdata` from hardware ID registers, user/syscfg/perf selection mutates `struct etmv4_config`, hardware enable programs the register fields from that config, and CPU power loss or low-power handling uses `struct etmv4_save_state` to preserve trace registers. Access wrappers insert architecture barriers around non-relaxed operations, which matters for ordering trace register programming around enable and disable.

## Dependencies And Integration Points
The header depends on `coresight-priv.h`, `asm/sysreg.h`, bitfield helpers, raw spinlocks, and CoreSight framework types. It integrates with the ETM sysfs groups through `coresight_etmv4_groups`, with trace-id lifecycle through `etm4_release_trace_id()`, and with architecture-specific system-register access through `etm4x_sysreg_read()` and `etm4x_sysreg_write()`.

## Risks And Test Signals
The highest-risk area is drift between architected register accessibility and the sysreg/MMIO case lists. A missing register in the sysreg switch can make valid sysreg-only hardware inaccessible; placing MMIO-only registers in sysreg paths can fault or read undefined values. Save-state coverage must track any register programmed during enable, or suspend/resume can silently lose trace configuration. Useful tests are build coverage on arm64, ETMv4 and ETE probe on sysreg and MMIO implementations, sysfs reads of management registers, low-power resume trace validation, and perf trace sessions that exercise trace IDs, filters, address comparators, and syscfg-selected features.
