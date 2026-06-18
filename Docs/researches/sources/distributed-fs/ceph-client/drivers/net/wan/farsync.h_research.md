# sources/distributed-fs/ceph-client/drivers/net/wan/farsync.h

Purpose: userspace-visible ABI header for the FarSync driver. It defines device names, the public version, private ioctl numbers, firmware download structure, configuration/status structure, valid-bit masks, card/line/protocol/state constants, TE1 configuration values, modem-signal bits, and optional debug flags.

Important APIs, types, and functions: primary exported data contracts are `struct fstioc_write` for firmware/card-memory writes and `struct fstioc_info` for `FSTGETCONF`/`FSTSETCONF`. Important constants include `FSTWRITE`, `FSTCPURESET`, `FSTCPURELEASE`, `FSTGETCONF`, `FSTSETCONF`, `FSTVAL_*`, `FST_TYPE_*`, `FST_*` state values, `V24`/`X21`/`V35`/`T1`/`E1`/`J1`, `FST_RAW`, `FST_GEN_HDLC`, modem input/output masks, and TE1 clocking/framing/coding/loop/buffer options.

Control flow: this header has no executable flow, but it determines how userspace drives `farsync.c`: reset the onboard CPU, write firmware blocks, release the CPU, poll/get config to complete startup, and set selected runtime options through valid-bit gated fields. `valid` is central: get operations report which fields are meaningful, while set operations request selective updates.

State and persistence: structures mirror live driver/card state rather than persistent storage. The constants are ABI-sensitive because several values overlap with firmware shared-memory configuration fields; changing them would break userspace tools or firmware expectations.

Dependencies and integration points: requires socket ioctl numbering from the kernel UAPI context and is consumed by `farsync.c` plus external FarSync configuration utilities. TE1 values map onto firmware `suConfig`/`suStatus` fields, and generic HDLC protocol selection maps to Linux WAN ioctl behavior.

Risks: the flexible array in `struct fstioc_write` must be used with careful userspace sizing. `struct fstioc_info` is large and version-sensitive; field additions must preserve compatibility. The `valid` mask excludes debug from `FSTVAL_ALL`, so callers must explicitly request or interpret debug behavior.

Test signals: ABI tests should verify ioctl numbers, structure sizes/offsets for target architectures, `FSTGETCONF` zeroed-input behavior, valid mask semantics, TE1 value mapping, and compatibility with existing FarSync firmware loading tools.
