# sources/distributed-fs/ceph-client/drivers/reset/reset-eyeq.c

Purpose: Mobileye EyeQ5/EyeQ6 reset provider for OLB-hosted reset domains exposed through auxiliary devices.

Important APIs/types/functions: `enum eqr_domain_type`, `struct eqr_domain_descriptor`, `struct eqr_match_data`, `struct eqr_private`, `eqr_busy_wait_locked()`, `eqr_assert_locked()`, `eqr_deassert_locked()`, `eqr_status()`, `eqr_of_xlate_internal()`, and `eqr_probe()`.

Control flow: auxiliary IDs select devices created by the EyeQ clock/OLB driver. Probe matches the reused OF node manually, gets platform-data base, initializes one mutex per domain, chooses one-cell or two-cell xlate, counts valid reset bits, and registers. Each operation decodes ID into domain/offset and applies domain-type-specific register sequences. SARCR and ACRP paths poll status; PCIE does not; EyeQ6H keeps reset and clock request registers synchronized.

State and persistence: OLB registers store state. Per-domain mutexes serialize read-modify-write and long LBIST-related waits.

Dependencies and integration: auxiliary bus, OF match tables, MMIO, bitfield helpers, reset framework, and parent OLB/clock device setup.

Risks and test signals: domain valid masks, status polarity, and busy-wait timeouts are high risk. Test every compatible, one/two-cell xlate, invalid reset rejection, EyeQ6H clock/reset sync, and timeout behavior during LBIST.
