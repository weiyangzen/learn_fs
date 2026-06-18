# sources/distributed-fs/ceph-client/drivers/pps/generators/Kconfig

Purpose: configuration menu for PPS signal generators.

Important entries: `PPS_GENERATOR` builds generator core `pps_gen_core`; `PPS_GENERATOR_DUMMY` builds a debug generator; `PPS_GENERATOR_TIO` depends on x86 Intel CPU support and targets Intel Time-Aware IO hardware.

Control flow/state: configuration-only. TIO help states it needs specialized external hardware to observe pulses.

Dependencies/integration: PPS generator core, x86 CPU feature support, and platform/ACPI hardware for TIO.

Risks/test signals: confirm generator core can be modular, dummy and TIO module names match help text, TIO is hidden on non-x86/non-Intel builds, and `PPS_DEBUG` affects generator compilation through Makefile flags.
