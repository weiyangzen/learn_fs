# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/cs_dsp.h

## Purpose
This private header provides local declarations for the Cirrus DSP driver implementation. At present it only exposes the KUnit-visible message-rate hook to sibling compilation units when KUnit is enabled.

## Important APIs, Types, And Functions
The header guard is `FW_CS_DSP_H`. Under `IS_ENABLED(CONFIG_KUNIT)`, it declares `bool cs_dsp_can_emit_message(void);`, implemented in `cs_dsp.c` as a KUnit-static-stub-capable rate-limit gate for noisy error-path tests. No structs or production-only APIs are declared here; public APIs are in `linux/firmware/cirrus/cs_dsp.h`.

## Control Flow, State, And Persistence
There is no state. Its only behavioral impact is compile-time: KUnit builds can reference or stub `cs_dsp_can_emit_message()`, while non-KUnit builds avoid exposing the declaration.

## Dependencies And Integration Points
The header is included by `cs_dsp.c` and potentially local test-aware code. It depends on Kconfig's `CONFIG_KUNIT` and the function's `VISIBLE_IF_KUNIT`/`EXPORT_SYMBOL_IF_KUNIT` implementation.

## Risks And Test Signals
Risk is low. The main signal is that KUnit builds compile and can redirect `cs_dsp_can_emit_message()`, while non-KUnit builds do not leak unnecessary symbols or declarations.
