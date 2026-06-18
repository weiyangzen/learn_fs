# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ptp.h

## Purpose
`idpf_ptp.h` declares the IDPF PTP and hardware timestamping data model and public interface. It defines PTP direct-register metadata, access modes, secondary mailbox info, TX timestamp latch tracking, vport timestamp capabilities, adapter-level PHC state, device timer results, inline capability checks, and stub implementations for builds without `CONFIG_PTP_1588_CLOCK`.

## Important APIs, types, and functions
- Register and command metadata: `struct idpf_ptp_cmd` and `struct idpf_ptp_dev_clk_regs`.
- Access classification: `enum idpf_ptp_access`.
- Mailbox and timer data: `struct idpf_ptp_secondary_mbx` and `struct idpf_ptp_dev_timers`.
- TX timestamp tracking: `enum idpf_ptp_tx_tstamp_state`, `struct idpf_ptp_tx_tstamp_status`, `struct idpf_ptp_tx_tstamp`, and `struct idpf_ptp_vport_tx_tstamp_caps`.
- Adapter PTP state: `struct idpf_ptp`.
- Helpers: `idpf_ptp_info_to_adapter()`, `idpf_ptp_is_vport_tx_tstamp_ena()`, and `idpf_ptp_is_vport_rx_tstamp_ena()`.
- Public prototypes or stubs: PTP lifecycle, capability negotiation, device/cross time mailbox operations, clock set/adjust operations, vport timestamp capability fetch, TX timestamp retrieval/request, timestamp mode set, timestamp extension, and timestamp work handler.

## Control flow
This header has no standalone runtime flow. With `CONFIG_PTP_1588_CLOCK`, it exposes real functions implemented in `idpf_ptp.c` and virtchnl PTP code. Without that config, it compiles inline no-op or `-EOPNOTSUPP` stubs so the rest of the driver can call PTP hooks conditionally without littering call sites with preprocessor checks.

## State and persistence behavior
The structs define where PTP state persists during driver runtime: PHC clock info and handle, cached PHC time and jiffies, register pointers, capability bits, feature access modes, secondary mailbox identity, TX latch free/in-use lists, per-latch skb state, and per-vport timestamp capability metadata. All state is volatile driver memory negotiated or initialized at probe/reset time.

## Dependencies and integration points
The header includes `linux/ptp_clock_kernel.h` and depends on kernel skb/list/spinlock types through included driver headers. It is included by `idpf_ptp.c`, `idpf_ethtool.c`, `idpf_lib.c`, and datapath code that requests or extends timestamps. It also declares mailbox-backed PTP helpers implemented in virtchnl-related files.

## Risks and edge cases
- Stub signatures must exactly match real-function signatures; any drift can create config-dependent build failures.
- Inline capability checks are intentionally simple pointer/access checks; callers still need vport/link/control locking where required.
- The flexible-array `tx_tstamp_status[]` in `idpf_ptp_vport_tx_tstamp_caps` requires correct allocation sizing by capability negotiation code.
- Direct register pointers must be initialized before direct access modes are used.

## Test signals
Build with PTP enabled and disabled, compile all call sites under both configs, validate timestamp capability checks before and after vport timestamp capability negotiation, exercise TX latch allocation sizing, and inspect static analysis for flexible-array allocation and register-pointer initialization.
