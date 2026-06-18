# sources/distributed-fs/ceph-client/include/linux/mfd/intel_pmc_bxt.h

Purpose: This header exposes the Intel Broxton PMC MFD interface for global configuration register access and S0ix telemetry.

Important APIs, types, and functions: Register macros define PMC GCR configuration, deep S0ix telemetry, and shallow S0ix telemetry offsets. `PMC_CFG_NO_REBOOT_EN` identifies the no-reboot bit. `struct intel_pmc_dev` stores the parent device, SCU IPC device, MMIO base for GCR registers, spinlock for GCR serialization, and optional telemetry SSRAM resource. If `CONFIG_MFD_INTEL_PMC_BXT` is enabled, exported helpers read 64-bit GCR values, update GCR bitfields, and read S0ix counters; otherwise inline stubs return `-ENOTSUPP`.

Control flow, state, and persistence: Consumers call helper functions to serialize register updates under `gcr_lock` and read telemetry. Persistent hardware state includes PMC config bits and telemetry counters; the struct tracks live mapping and IPC dependencies.

Dependencies and integration points: It integrates with Intel SCU IPC, PMC platform code, power management telemetry, and drivers that need no-reboot or S0ix information.

Risks and test signals: Risks include using helpers when the config is disabled, missing spinlock protection for GCR access, wrong telemetry resource mapping, and confusing shallow/deep S0ix counters. Test signals include compile coverage with PMC enabled and disabled, GCR update readback, S0ix counter reads across suspend cycles, and lockdep around concurrent GCR updates.
