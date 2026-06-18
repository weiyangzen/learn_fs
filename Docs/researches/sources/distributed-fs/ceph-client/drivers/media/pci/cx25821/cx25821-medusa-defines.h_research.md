# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-defines.h

Purpose: defines Medusa decoder identifiers and small constants shared by Medusa video programming.

Important APIs and constants: decoder IDs `VDEC_A` through `VDEC_H` map to 0-7. `END_OF_SEQ` is `0xF`. `MAX_REGISTRY_SZ` is defined as `40;`.

Control flow: Medusa functions use decoder IDs for switch statements and register offset calculations.

State and persistence: no state; compile-time constants only.

Dependencies and integration points: included by `cx25821-medusa-video.h`, which is included by Medusa implementation and indirectly by control paths.

Risks: `MAX_REGISTRY_SZ` includes a semicolon in the macro body, which is harmless only in statement-like contexts and risky in expressions. Decoder IDs must stay aligned with `MAX_DECODERS` and register block spacing in `cx25821-medusa-reg.h`.

Test signals: compile coverage and Medusa per-decoder control tests across all decoder IDs.
