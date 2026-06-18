# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/lparcfg.c

## Purpose
Creates `/proc/powerpc/lparcfg`, a pSeries partition configuration and entitlement interface. It reports processor, memory, capacity, pool, CMO, dispatch, power, security, and identity data, and on SPLPAR systems allows selected entitlement/weight updates.

## Important APIs, Types, And Functions
The main proc handlers are `lparcfg_open`, `lparcfg_data`, `pseries_lparcfg_data`, and `lparcfg_write`. Data collection helpers include `h_get_ppp`, `parse_ppp_data`, `parse_mpp_data`, `parse_mpp_x_data`, `read_lpar_name`, `parse_system_parameter_string`, `pseries_cmo_data`, `splpar_dispatch_data`, `parse_em_data`, `maxmem_data`, and `show_gpci_data`. Update paths are `update_ppp` and `update_mpp`.

## Control Flow
Reads emit module/version, system model, serial, partition id, then SPLPAR-specific or dedicated-processor capacity data. SPLPAR reads combine PAPR system parameters, H_GET_PPP/H_PIC processor data, H_GET_MPP/H_GET_MPP_X memory data, lppaca counters, PURR/TB values, and security flavor. Writes parse `name=value` pairs for `partition_entitled_capacity`, `capacity_weight`, `entitled_memory`, and `entitled_memory_weight`; they call H_SET_PPP or H_SET_MPP and translate common hcall returns to errno or byte count.

## State And Persistence
The file stores `boot_pool_idle_time` captured at init. Other displayed state is read live from firmware, device tree, lppaca, CMO, VIO, and memory metadata. Writes persist entitlement changes in the hypervisor partition configuration rather than kernel-local durable storage.

## Dependencies And Integration Points
Depends on procfs/seq_file, PAPR sysparm helpers, hcall wrappers, RTAS/device tree properties, lppaca counters, `h_get_mpp` from `lpar.c`, CMO helpers, VIO CMO entitlement validation, hugepage and dynamic memory metadata, and VAS CPU DLPAR reconfiguration after processor entitlement updates.

## Risks And Edge Cases
Input parsing is intentionally narrow and truncates at 64 bytes. Failed H_PIC at boot affects since-boot pool-idle statistics. Firmware or QEMU may omit the dynamic LPAR name, forcing a device-tree fallback. Entitlement writes can return constrained success, busy, hardware, or parameter errors. Memory entitlement writes must be accepted by VIO before changing firmware state.

## Test Signals
Read `/proc/powerpc/lparcfg` on SPLPAR and non-SPLPAR guests, with CMO/XCMO enabled and disabled. Test writes for all accepted keys, invalid formats, non-SPLPAR writes, H_BUSY/H_PARAMETER fault injection, VAS reconfiguration on processor entitlement changes, and lparstat compatibility fields.
