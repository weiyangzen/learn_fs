# sources/distributed-fs/ceph-client/arch/alpha/kernel/pc873xx.c

**Purpose:** Detects and configures National Semiconductor PC873xx Super I/O chips on Alpha platforms. It probes known config-port bases, identifies chip models, and enables selected parallel/IDE features.

**Important APIs/types/functions:** Exposes `pc873xx_probe()`, `pc873xx_get_base()`, `pc873xx_get_model()`, `pc873xx_enable_epp19()`, and `pc873xx_enable_ide()`. Internal helpers are `pc873xx_read()` and `pc873xx_write()`. State includes static `base` and `model`, probe ports `0x398` and `0x26e`, and model-name table.

**Control flow:** `pc873xx_probe()` iterates probe bases, reserves two I/O ports with `request_region()`, reads `REG_SID`, matches bit patterns to PC87332/PC87306/PC87334/PC87303, and releases the region if no match. Feature functions read the configured base register, print an informational message, and write updated control bits: `pc873xx_enable_epp19()` sets PCR mode bits to EPP v1.9, while `pc873xx_enable_ide()` sets bit `0x40` in FER. Writes disable local interrupts and write the data byte twice as required by the chip.

**State and persistence behavior:** Stores detected base/model in static variables and mutates Super I/O configuration registers. The requested I/O region remains held after successful probe. No filesystem persistence.

**Dependencies and integration points:** Uses constants from `pc873xx.h`, Alpha port I/O, Linux I/O resource reservation, and platform setup code that calls probe/enable functions.

**Risks:** Probe only recognizes a subset of possible models and returns `1` or `-1` rather than normal `0/-errno`. `pc873xx_get_model()` assumes `model` is valid and should not be called before successful probe. Feature writes assume the selected chip has compatible registers.

**Test signals:** On target boards, confirm probe base, model string, retained I/O resource, EPP mode configuration, and IDE interrupt enablement. Negative tests should cover both probe ports unavailable or unknown SID values.
