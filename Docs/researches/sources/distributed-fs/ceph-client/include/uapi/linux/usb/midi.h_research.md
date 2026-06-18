# sources/distributed-fs/ceph-client/include/uapi/linux/usb/midi.h

Purpose: Defines USB MIDI 2.0 group terminal block descriptor constants and structures.

Important APIs/types/functions: Constants describe MIDI streaming descriptor subtypes and group terminal block types/protocols. Structures model group terminal block descriptors and block headers with fields for block ID, group terminal count, group counts, protocol, maximum input/output bandwidth, and string indices.

Control flow: USB MIDI host/gadget code parses descriptors during enumeration to discover MIDI 2.0 group terminal blocks and supported protocols/bandwidth.

State and persistence behavior: Descriptor data is static capability advertisement. Runtime MIDI stream state lives in class drivers and endpoints.

Dependencies and integration points: Includes USB audio/MIDI class context and Linux types; integrates with ALSA rawmidi/UMP support and USB gadget MIDI functions.

Risks: Descriptor lengths and protocol values must match USB MIDI spec revisions. Misreported bandwidth/group counts can break host routing.

Test signals: Parse MIDI 1.0 and MIDI 2.0 descriptors, enumerate gadget MIDI devices, verify group terminal counts/protocols, and fuzz descriptor length/count mismatches.
