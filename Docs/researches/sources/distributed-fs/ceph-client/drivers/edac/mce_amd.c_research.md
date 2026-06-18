# sources/distributed-fs/ceph-client/drivers/edac/mce_amd.c Research

## Purpose
`mce_amd.c` is the in-kernel AMD/Hygon Machine Check Exception decoder used by EDAC. It registers an early MCE notifier, decodes legacy AMD MCA banks by CPU family, decodes Scalable MCA bank types on newer CPUs, prints detailed hardware-error diagnostics, and exposes a callback hook so memory-controller EDAC drivers can add DRAM ECC address/location decoding.

## Important APIs, Types, and Functions
The exported hook pair `amd_register_ecc_decoder()` and `amd_unregister_ecc_decoder()` manages the global `decode_dram_ecc` callback. `pp_msgs` is also exported for other AMD EDAC code. `struct amd_decoder_ops fam_ops` stores family-specific decoders for MC0/MC1/MC2; `mce_amd_init()` selects K8, Family 10h/11h/12h/14h/15h/16h implementations and the extended-error-code mask.

Legacy bank decoders include `decode_mc0_mce()` through `decode_mc6_mce()`, backed by family-specific helpers such as `k8_mc0_mce()`, `f15h_mc1_mce()`, and `f16h_mc2_mce()`. `decode_mc4_mce()` handles northbridge/DRAM ECC errors and invokes `decode_dram_ecc()` for supported DRAM ECC xEC values. `decode_smca_error()` uses `smca_get_bank_type()` and `smca_long_names[]` to report Scalable MCA units and invokes the DRAM ECC callback for UMC/UMC_V2 errors with xEC 0.

`amd_decode_mce()` is the notifier body. It prints severity from `decode_error_status()`, status flags, address/PPIN/IPID/syndrome/FRU text when valid, dispatches SMCA or legacy bank-specific decode, prints generic error-code fields through `amd_decode_err_code()`, marks the MCE handled, and returns `NOTIFY_OK`.

## Control Flow
`early_initcall(mce_amd_init)` runs on boot/module init. It rejects non-AMD/Hygon CPUs and hypervisors, chooses SMCA or legacy family support, logs enablement, and registers `amd_mce_dec_nb` with priority `MCE_PRIO_EDAC`. At MCE time, already-CEC-handled records are ignored. SMCA systems use bank type decoding; older systems switch on `m->bank`. Module builds unregister the notifier on exit.

## State and Persistence
State is global and in-memory: selected decoder ops, `xec_mask`, the optional DRAM ECC callback, and notifier registration. The module writes kernel log diagnostics but no persistent state. It does not clear hardware MCE registers; it decodes records supplied by the x86 MCE core.

## Dependencies and Integration Points
The file depends on x86 CPU feature/family helpers, MCE structures/status bits, SMCA bank-type helpers, MSR reads, kernel notifier APIs, EDAC priority conventions, and `mce_amd.h` macros. Its callback hook is used by AMD memory-controller EDAC drivers to enrich DRAM ECC reports.

## Risks and Edge Cases
The callback pointer is global and not locked; registration order assumes EDAC module lifecycle discipline. Unsupported families 17h/18h without SMCA return `-EINVAL`. Logging uses `pr_emerg()`/`pr_cont()` sequences, so malformed interleaving can affect readability. SMCA FRU text is copied from vendor syndrome fields and treated as a 16-byte string. Incorrect xEC masks or bank-type mappings lead to misleading diagnostics rather than failed handling.

## Test Signals
Test with synthetic MCE records or hardware injection should cover SMCA UMC errors invoking the DRAM callback, legacy family bank 0-6 decode paths, corrected/deferred/uncorrected/fatal status messages, address/IPID/syndrome/FRU printing, ignored `MCE_HANDLED_CEC` records, callback register/unregister warning behavior, and notifier unregister for module builds.
