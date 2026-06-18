# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/IOGEAR__Kaliber-MMOmentum.bpf.c

## Purpose
This small descriptor quirk enables the extra buttons on the IOGEAR Kaliber Gaming MMOmentum Pro mouse. The original descriptor marks several button groups as constants, so Linux only exposes five of the twelve physical buttons.

## Important APIs, Types, And Functions
The match is USB VID `0x258A`, PID `0x0027`. `hid_fix_rdesc()` is the only runtime hook. It obtains descriptor data with `hid_bpf_get_data()` and edits offsets 84, 112, and 140. `HID_BPF_OPS(iogear_kaliber_momentum)` installs only `.hid_rdesc_fixup`. `probe()` binds only to descriptor size 213.

## Control Flow
The descriptor hook first checks `data[3] == 0x06` to limit changes to the keyboard interface. For each known offset, it changes an Input item from `0x81 0x03` (Constant, Variable, Absolute) to `0x81 0x02` (Data, Variable, Absolute). It returns 0 because it edits the descriptor in place without changing size.

## State And Persistence
There is no mutable state beyond the in-place descriptor bytes.

## Dependencies And Integration Points
The program depends on HID-BPF helpers and the fixed descriptor layout for the target mouse's keyboard interface. It integrates before normal HID parsing so the kernel exposes additional button inputs.

## Risks
The VID is shared by other vendors, so the descriptor-size and keyboard-interface checks are important but still layout-specific. If a firmware variant has the same size but different offset contents, the code safely checks `0x81 0x03` before editing, but may leave buttons unfixed.

## Test Signals
A descriptor dump should show offsets 84/112/140 changed from constant inputs to data inputs. Functional testing should confirm all twelve mouse buttons are visible and no unrelated interface with a different descriptor size binds.
