# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/sie.h

## Purpose
s390 SIE intercept decoding data for tools and trace/user interfaces.

## Important APIs, Types, and Functions
Defines macro tables for diagnose codes, SIGP orders, program interruption codes, interceptable instruction codes, and SIE intercept codes. Helper macros `exit_code_ipa0()`, `exit_code()`, `INSN_DECODE_IPA0()`, `INSN_DECODE()`, and `icpt_insn_decoder()` create table entries and decode intercepted instruction keys.

## Control Flow, State, and Persistence
There is no storage. Consumers expand the tables into lookup arrays and use `icpt_insn_decoder(insn)` as a conditional-expression decoder suitable for trace declarations where general C control flow is undesirable.

## Dependencies and Integration Points
Integrated with s390 KVM/SIE tracing and userspace tools that need stable intercept names. It intentionally avoids switch/if constructs for parser friendliness.

## Risks and Test Signals
Risks include incomplete instruction coverage, decoder bit-shift mistakes for different opcode formats, and userspace parsers depending on macro shape. Test signals are decode golden tests for each IPA0 group, tracepoint build checks, and lookup coverage for diagnose/SIGP/program codes.
