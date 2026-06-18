# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-i2s.h

Purpose: declares the PXA2xx I2S sysclk ID.

Important APIs/types/functions: defines `PXA2XX_I2S_SYSCLK` as clock ID 0.

Control flow: no executable flow; machine drivers pass this ID to `snd_soc_dai_set_sysclk`.

State and persistence: no state.

Dependencies and integration: used by `pxa2xx-i2s.c` and the Spitz machine driver.

Risks: minimal; value changes would break machine-driver clock API expectations.

Test signals: compile coverage and machine-driver hw_params calling the I2S sysclk API.
