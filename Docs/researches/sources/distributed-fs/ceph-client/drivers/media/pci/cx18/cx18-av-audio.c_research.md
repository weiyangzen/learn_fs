<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-audio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-audio.c

Purpose: Implements audio path, clock, and V4L2 audio control handling for the cx18 internal A/V decoder block.

Important APIs/functions: `set_audclk_freq()` programs PLL, sample-rate converter, MCLK, audio/video count registers for 32/44.1/48 kHz and for serial versus analog demod inputs. `cx18_av_audio_set_path()` stops the audio microcontroller, resets the audio path, mutes, selects serial or analog demod path, programs audio clock, deasserts reset, and restarts the microcontroller for tuner audio. `cx18_av_s_clock_freq()` changes clock frequency through reset/mute sequencing. Control helpers set volume, bass, treble, balance, and mute. `cx18_av_audio_ctrl_ops` exports the V4L2 control callback.

Control flow: Input routing in `cx18-av-core.c` updates `state->aud_input` and calls `cx18_av_audio_set_path()`. Audio clock changes validate the requested rate, temporarily stop/reset relevant blocks, program PLL/SRC values, and restart. V4L2 audio controls translate generic ranges into CXADEC register values.

State/persistence: `cx->av_state.aud_input` selects serial versus analog behavior; `audclk_freq` caches selected sample rate; control values live in V4L2 control state and hardware registers. Hardware register settings persist until reconfigured/reset.

Dependencies/integration: Uses cx18 AV register helpers from `cx18-av-core.c`, V4L2 control framework, and `cx18_av_state`. It cooperates with video standard/input changes because analog audio autodetection depends on the microcontroller and selected standard.

Risks: PLL/SRC values are hard-coded magic constants and comments document sync sensitivity. Mute handling differs for analog and serial audio because the microcontroller can overwrite mute registers. Unsupported rates return `-EINVAL`. Register sequencing is important to avoid audible artifacts.

Test signals: 32/44.1/48 kHz clock changes, tuner versus line/serial audio, mute/unmute, volume/bass/treble/balance controls, audio/video sync, and absence of pops during path changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-audio.c -->
