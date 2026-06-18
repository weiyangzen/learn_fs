# sources/distributed-fs/ceph-client/include/uapi/linux/patchkey.h

Purpose: Preserves the `_PATCHKEY()` macro ABI used by legacy OSS/AWE sound patch structures while discouraging direct inclusion.

Important APIs/types/functions: Enforces indirect inclusion through `_LINUX_PATCHKEY_H_INDIRECT`, includes `<endian.h>` for userspace, and defines `_PATCHKEY(id)` differently for big- and little-endian byte order.

Control flow: No runtime flow. At preprocessing time, consumers included via `<sys/soundcard.h>` or `<linux/soundcard.h>` obtain an endian-correct patch key value.

State and persistence behavior: No runtime state. The macro encodes persistent binary patch identifiers in the endian layout expected by old userspace and driver interfaces.

Dependencies and integration points: Integrates with OSS soundcard headers and legacy AWE voice/patch userspace. It depends on userspace byte-order macros when not compiling in the kernel.

Risks: Direct include intentionally fails, so packaging or include-order changes can break builds. Incorrect byte-order detection changes binary patch identifiers and breaks legacy sound data exchange.

Test signals: Compile OSS userspace on little- and big-endian targets through the supported include path, verify direct inclusion errors, and compare `_PATCHKEY()` output against historical soundcard ABI expectations.
