# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_focusrite.c

Purpose: supplies Focusrite Saffire and Saffire Pro BeBoB specs for clock source, sampling rate, and meter handling using Focusrite-specific register addresses.

Important APIs/functions: `saffire_read_block`, `saffire_read_quad`, `saffire_write_quad`, `saffirepro_both_clk_freq_get`, `saffirepro_both_clk_freq_set`, `saffirepro_both_clk_src_get`, `saffire_both_clk_src_get`, and `saffire_meter_get`. It exports `saffirepro_26_spec`, `saffirepro_10_spec`, `saffire_le_spec`, and `saffire_spec`.

Control flow and state: Focusrite specs bind function pointers into `snd_bebob_spec`. Pro devices read/write a rate selector register and map hardware clock-source fields to internal clock IDs. Non-Pro Saffire devices use generic BeBoB stream rate functions and read a smaller clock source register. Meter reads convert big-endian blocks and reorder Saffire LE channels.

Dependencies/integration: integrated from `bebob.c` device table and used by proc meter/clock reporting and PCM rate decisions. Risks include hard-coded offsets, clock source map divergence between Pro 10 and Pro 26, missing validation for unsupported external lock, and channel reorder assumptions. Test signals are correct proc clock/meter output, accepted rate changes without reboot for Pro devices, and no out-of-range clock ID returns.
