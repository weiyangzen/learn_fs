# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Logitech__SpaceNavigator.bpf.c

## Purpose
This descriptor quirk fixes 3Dconnexion/Logitech SpaceNavigator units whose six axes are absolute but declared as relative. The kernel had a historical fix for some variants, but the offsets differ across devices, so this BPF program tries all known offsets for descriptor sizes seen in the field.

## Important APIs, Types, And Functions
The match is USB Logitech VID `0x046D`, PID `0xC626`, `HID_GROUP_ANY`. `hid_fix_rdesc()` edits Input item flags at offsets 32, 36, 49, and 53 when they are `0x81 0x06`. `probe()` accepts descriptor sizes 202, 217, and 228 and refuses to load if the descriptor already appears fixed.

## Control Flow
At descriptor-fixup time, each candidate offset is inspected independently. If an item is `Input(Data,Var,Rel)`, the second byte is changed to `0x02` for `Input(Data,Var,Abs)`. Probe first filters unknown descriptor sizes, then checks both known offset pairs; if either pair is already absolute, it returns `-EINVAL` to avoid double-fixing.

## State And Persistence
The program is stateless after descriptor mutation.

## Dependencies And Integration Points
It depends on HID-BPF helpers and known SpaceNavigator descriptor layouts. It integrates with the HID parser so the evdev axis semantics are absolute rather than relative for X/Y/Z and Rx/Ry/Rz collections.

## Risks
The 2009 model size is not known and future variants may need additional offsets. The current code is conservative because it only changes bytes that match `0x81 0x06`, but an unknown same-size layout could remain unfixed.

## Test Signals
Tests should cover descriptor sizes 202, 217, and 228, already-fixed descriptors, and each offset pair. Runtime verification should show stable absolute 6-axis values rather than accumulating relative deltas.
