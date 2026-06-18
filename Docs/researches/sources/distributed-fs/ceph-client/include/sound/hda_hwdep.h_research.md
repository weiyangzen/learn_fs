# sources/distributed-fs/ceph-client/include/sound/hda_hwdep.h

Source read summary: 31 lines, userspace hwdep ioctl ABI for HD-audio verbs.

Purpose: exposes the version and ioctl payloads used by ALSA hwdep devices to issue raw HD-audio verbs and query widget capabilities.

Important APIs, types, and functions: `HDA_HWDEP_VERSION` encodes 1.0.0. `HDA_VERB(nid, verb, param)` packs NID, verb, and parameter using the documented shifts. `struct hda_verb_ioctl` carries the command and response. Ioctls are `HDA_IOCTL_PVERSION`, `HDA_IOCTL_VERB_WRITE`, and `HDA_IOCTL_GET_WCAP`.

Control flow: a userspace diagnostic or reconfiguration tool opens the codec hwdep device, packs a verb, submits ioctl, and receives the response or widget capability value from the kernel codec implementation.

State and persistence behavior: the header stores no state. Issued verbs may mutate codec hardware state; persistence is limited to hardware registers and whatever the codec driver later caches or restores.

Dependencies and integration points: relies on Linux ioctl encoding and is consumed by HD-audio hwdep implementation and tools such as codec dump/reconfig utilities.

Risks and edge cases: raw verbs can put codecs into unsupported states, ABI packing must remain stable, and 32-bit compatibility must preserve the two `u32` fields exactly.

Test signals: ioctl version checks, raw read/write verbs against a known codec, invalid NID/verb handling, compat ioctl coverage, and permission/access tests for hwdep exposure.
