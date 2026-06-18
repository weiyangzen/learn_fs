# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_csr.h

Purpose: defines the NITROX CNN55XX CSR address map and bitfield overlays for engine clusters, microcode loader, AQM queues, NPS packet/core units, POM/BMI/BMO/EFL/LBC, reset/fuse registers, and interrupt status/enable registers.

Important APIs and types: register macros include EMU, UCD, AQM/AQMQ, NPS_CORE, NPS_PKT input/solicit/mailbox, POM, BMI, EFL, BMO, LBC, `RST_BOOT`, and `FUS_DAT1`. Union overlays include queue doorbells/sizes/completions/enables, fuse maps, core enables, interrupt masks, NPS packet counters, NPS core active/status, mailbox interrupt state, RNG, BMI/BMO/POM/LBC controls, invalidation status, reset boot frequency, and fuse data.

Control flow and state: no executable code; the header maps persistent hardware state into C fields consumed by HAL, ISR, SR-IOV, mailbox, and request manager code. Endian-specific bitfields control how values are assembled for `readq()`/`writeq()`.

Dependencies and integration points: depends on Linux types and byteorder. HAL uses it to initialize hardware units, ISR uses it to clear errors and re-enable rings, and debug/device info code uses fuse and reset fields.

Risks and test signals: risks include bitfield layout portability, register-offset drift across NITROX revisions, W1C/W1S fields being accessed with read-modify-write where write-only semantics matter, and large all-ones interrupt enables exposing noisy error storms. Test signals include hardware info decoding, queue enable/doorbell programming, NPS interrupt clearing, LBC invalidation completion, mailbox interrupt bits, and builds on endian variants.
