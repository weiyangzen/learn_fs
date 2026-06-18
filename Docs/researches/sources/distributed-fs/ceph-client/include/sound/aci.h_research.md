# sources/distributed-fs/ceph-client/include/sound/aci.h

## Purpose
`aci.h` defines the command protocol and state for the Miro/Pinnacle ACI mixer interface. It provides register offsets, command ids for tuner, mute, amplifier, equalizer, IDE/WSS, and status operations, and the small driver context used by ACI command helpers.

## Important APIs, Types, and Functions
Important macros include `ACI_REG_COMMAND`, `ACI_REG_STATUS`, `ACI_REG_BUSY`, timeout `ACI_MINTIME`, command opcodes such as `ACI_SET_MUTE`, `ACI_SET_POWERAMP`, `ACI_READ_VERSION`, and mixer get/set opcodes for master, MIC, line, CD, synth, PCM, radio lines, and EQ bands. `struct snd_miro_aci` stores card pointer, I/O port, ids, amplifier/preamp/solo state, and `aci_mutex`. APIs are `snd_aci_cmd()` and `snd_aci_get_aci()`.

## Control Flow
Drivers serialize through `aci_mutex`, write command bytes to the command register, poll status/busy registers within the timeout, then update cached board feature fields or return readback values.

## State and Persistence Behavior
The context tracks runtime board identity and user-visible amplifier/preamp/solo settings. Hardware state lives in the external ACI device and is not persisted by this header.

## Dependencies and Integration Points
The header integrates old ALSA Miro sound-card code with ISA I/O port access and ALSA card/control code. The card type determines which command subset is meaningful.

## Risks and Test Signals
Risks include timeout sensitivity, wrong left/right opcode offsets, missing mutex coverage around multi-byte commands, and unsupported command handling. Test signals include mixer read/write round trips, tuner stereo/station reads, init/status failure paths, and concurrent mixer access.
