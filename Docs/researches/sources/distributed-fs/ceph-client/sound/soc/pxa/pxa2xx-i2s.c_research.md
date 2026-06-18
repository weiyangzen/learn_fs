# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-i2s.c

Purpose: implements the legacy PXA2xx I2S CPU DAI and component using the PXA2xx PCM library.

Important APIs/types/functions: global `struct pxa_i2s_port pxa_i2s`, `clk_i2s`, `clk_ena`, and `i2s_reg_base` hold controller state. DAI ops include `pxa2xx_i2s_set_dai_fmt`, `pxa2xx_i2s_hw_params`, `pxa2xx_i2s_trigger`, startup/shutdown, probe/remove, and PM save/restore.

Control flow: platform probe maps registers and sets DMA FIFO addresses. DAI probe gets `I2SCLK`, resets the controller, disables replay/record, and initializes DMA data. hw_params enables the clock, selects DMA data, programs master/format/FIFO thresholds, enables service interrupts, and sets `SADIV` for supported rates. Trigger starts by enabling replay/record and `SACR0_ENB`; shutdown disables the stream direction and turns off the clock when both directions are disabled.

State and persistence: controller state is global, so it assumes one I2S controller instance. PM snapshots `SACR0/SACR1/SAIMR/SADIV`. DMA data structures are static.

Dependencies and integration: uses `sound/pxa2xx-lib` PCM callbacks, `pxa2xx-i2s.h`, platform resources, and fixed-rate divider programming.

Risks: `if (!(SACR0 & SACR0_ENB))` appears to test the register-offset macro rather than the register value, so inactive configuration logic is effectively wrong. Global state prevents multiple independent instances. Unsupported formats are not explicitly rejected in `set_dai_fmt` for all default cases.

Test signals: stereo 16-bit playback/capture at all listed rates, clock enable/disable balance, suspend/resume register restore, and regression coverage for the inactive-port configuration condition.
