# sources/distributed-fs/ceph-client/sound/firewire/dice/dice-pcm.c

Purpose: exposes DICE PCM devices, one per supported stream index, with dynamic constraints derived from detected low/middle/high channel maps and clock capabilities.

Important APIs/functions: `dice_rate_constraint`, `dice_channels_constraint`, `limit_channels_and_rates`, `init_hw_info`, PCM ops `pcm_open`, `pcm_close`, `pcm_hw_params`, `pcm_hw_free`, prepare/trigger/pointer/ack callbacks, and `snd_dice_create_pcm`.

Control flow and state: open locks streams, sets AM824 constraints, and pins rate/period/buffer when externally clocked or already reserved; high-rate dual-wire mode adjusts period/buffer units. `hw_params` reserves duplex resources and increments `substreams_counter`. Prepare starts all required DICE streams and prepares the selected AMDTP stream. Trigger toggles PCM pointer only for the selected stream.

Dependencies/integration: depends on DICE format detection arrays, transaction clock source/rate reads, stream reserve/start, AM824, ALSA PCM, and AMDTP domain pointer/ack. Risks include a capture prepare path returning 0 even if stream start fails, empty channel maps producing invalid constraints, dual-wire period scaling, and external-clock changes. Test signals are per-device PCM creation, valid constraints for each rate mode, high-rate playback/capture without underruns, and pointer/ack correctness.
