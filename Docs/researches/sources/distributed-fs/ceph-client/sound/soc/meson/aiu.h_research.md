# sources/distributed-fs/ceph-client/sound/soc/meson/aiu.h

Purpose: Defines shared AIU types, clock ids, platform flags, DAI operation externs, format masks, registration prototypes, DAI phandle helper prototype, and AIU register offsets.

Important APIs and types: `enum aiu_clk_ids` indexes pclk/aoclk/mclk/mixer clocks. `struct aiu_interface` groups clock bulk data and IRQ per I2S or SPDIF side. `struct aiu_platform_data` records SoC quirks such as internal acodec and newer I2S divider support. `struct aiu` is the root runtime state. The header declares `aiu_of_xlate_dai_name()`, control component registration functions, FIFO probe helpers, and extern DAI ops for FIFO and encoder variants.

Control flow: No executable logic. Constants define how sibling files address AIU registers such as `AIU_I2S_MISC`, `AIU_CLK_CTRL`, `AIU_MEM_I2S_*`, and `AIU_MEM_IEC958_*`.

State and persistence: Declares root and interface state stored by the platform driver. Register offsets correspond to persistent hardware state.

Dependencies and integration points: Included across AIU CPU, FIFO, encoder, and codec-control files. It is the internal ABI for the composite `snd-soc-meson-aiu` module.

Risks: Register offsets and clock index ordering must match device-tree clock lists and hardware manuals. `AIU_FORMATS` constrains all AIU CPU DAIs; adding formats requires validating every FIFO and encoder path.

Test signals: Build/link coverage of the composite AIU module, clock-name matching in DT, and runtime register access in all AIU subdrivers.
