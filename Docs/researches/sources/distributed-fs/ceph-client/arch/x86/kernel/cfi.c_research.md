# sources/distributed-fs/ceph-client/arch/x86/kernel/cfi.c

## Purpose
This file decodes and reports Clang kernel CFI failures on x86 for KCFI and FineIBT modes.

## Important APIs, Types, and Functions
`decode_cfi_insn()` decodes the compiler-generated KCFI trap sequence near `regs->ip`, extracts the expected type ID and target register value, and returns them to the caller. `handle_cfi_failure()` chooses KCFI or FineIBT decoding based on `cfi_mode`, validates the trap, and reports through `report_cfi_failure()` or `report_cfi_failure_noaddr()`. `__ADDRESSABLE(__memcpy)` forces a KCFI type symbol for memcpy.

## Control Flow
When a `ud2`/bug trap is being classified, `handle_cfi_failure()` checks the configured CFI mode. KCFI requires `is_cfi_trap()` and local instruction decoding from the preceding `movl/addl/je/ud2` sequence. FineIBT delegates to `decode_fineibt_insn()`. Successful decoding reports the target and expected type; unsupported cases return `BUG_TRAP_TYPE_NONE`.

## State and Persistence
The file has no mutable state. It reads kernel text and register state and delegates persistent reporting policy to the generic CFI subsystem.

## Dependencies and Integration Points
It depends on x86 instruction decoding, nofault kernel text reads, register offset evaluation, generic Linux CFI helpers, FineIBT decoding, and bug trap classification.

## Risks and Test Signals
Risks include compiler sequence drift, instruction decoder failures, wrong ModRM register extraction, and false positives for unrelated `ud2`. Test signals include KCFI/FineIBT selftests, deliberate CFI mismatch reporting with target/type, and non-CFI `ud2` traps still following normal bug handling.
