# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_llc.c Research

Purpose: this is a focused LLC/RPS selftest that verifies the firmware pcode ring-frequency table matches the driver-computed IA and ring frequencies over the supported GPU frequency range.

Important APIs/types/functions: `gen6_verify_ring_freq()` is the only substantive helper and `st_llc_verify()` is the exported selftest entrypoint declared in `selftest_llc.h`. It uses `struct intel_llc`, `struct ia_constants`, `struct intel_rps`, `get_ia_constants()`, `calc_ia_freq()`, `snb_pcode_read()`, and `intel_gpu_freq()`.

Control flow: `st_llc_verify()` calls `gen6_verify_ring_freq()`. The helper takes a runtime PM wakeref, fetches IA constants from the LLC code, and iterates from `consts.min_gpu_freq` to `consts.max_gpu_freq`. For each frequency it calculates expected IA and ring values, asks pcode for `GEN6_PCODE_READ_MIN_FREQ_TABLE`, extracts low and high bytes, and compares them against expectations. The loop stops on read failure or mismatch.

State and persistence: no persistent driver state is intentionally changed. The test temporarily holds runtime PM to make pcode access valid and reads firmware tables. It returns after releasing the wakeref.

Dependencies/integration: this file is a selftest facade over the production LLC and RPS frequency code. It validates the contract between software table generation and pcode-visible hardware state, including Gen9 scaling through `GEN9_FREQ_SCALER`.

Risks and test signals: failures indicate either pcode read failure (`-ENXIO`) or a mismatch between expected CPU/ring ratios and firmware-visible entries (`-EINVAL`). The test depends on valid IA constants and platforms where the pcode table is available; if constants cannot be obtained it exits without error. Diagnostic output includes GPU frequency in MHz and expected/found table fields.
