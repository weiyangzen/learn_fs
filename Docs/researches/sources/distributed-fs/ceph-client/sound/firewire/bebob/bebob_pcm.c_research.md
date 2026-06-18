# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_pcm.c

Purpose: exposes a duplex ALSA PCM device for BeBoB streams, deriving rates/channels from discovered stream formations and bridging PCM callbacks to AMDTP domain operations.

Important APIs/functions: hardware rules `hw_rule_rate` and `hw_rule_channels`, `limit_channels_and_rates`, `pcm_init_hw_params`, PCM ops `pcm_open`, `pcm_close`, `pcm_hw_params`, `pcm_hw_free`, prepare/trigger/pointer/ack callbacks, and `snd_bebob_create_pcm_devices`.

Control flow and state: open locks the stream, installs hardware constraints, checks clock source, and may pin rate/period/buffer to current values when externally clocked or already reserved. `hw_params` reserves duplex resources and increments `substreams_counter`; `hw_free` decrements and stops when no users remain. Prepare starts duplex streaming and prepares the direction-specific AMDTP stream. Trigger only toggles the active PCM pointer.

Dependencies/integration: uses BeBoB stream formation tables, spec rate/clock callbacks, AM824 constraints, ALSA PCM managed vmalloc buffers, and `amdtp_domain` pointer/ack. Risks include constraints with empty formations, external-clock rate changes during open, counter imbalance, and error propagation from capture prepare. Test signals include valid channel/rate constraint pairs, JACK-style period consistency, XRUN recovery through prepare, and correct capture/playback pointer movement.
