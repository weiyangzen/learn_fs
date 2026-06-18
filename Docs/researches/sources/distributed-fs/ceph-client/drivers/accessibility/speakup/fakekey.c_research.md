# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/fakekey.c Research

## Purpose
`fakekey.c` creates a virtual input keyboard used by Speakup to inject a synthetic Down Arrow key press into the input subsystem and to identify that synthetic key path.

## Important APIs And Control Flow
`speakup_add_virtual_keyboard()` allocates and registers an `input_dev` named `Speakup`. `speakup_remove_virtual_keyboard()` unregisters it. `speakup_fake_down_arrow()` emits press and release events for `KEY_DOWN` followed by `input_sync()`. Injection disables local interrupts, disables preemption, sets the per-CPU `reporting_keystroke` flag, reports key down/up/sync, clears the flag, then restores preemption and interrupts. `speakup_fake_key_pressed()` reads the per-CPU flag.

## State And Persistence
State consists of global `virt_keyboard` and per-CPU `reporting_keystroke`. It persists only while Speakup is loaded or initialized.

## Dependencies And Integration Points
The file depends on the Linux input subsystem, per-CPU variables, preemption and IRQ controls, and Speakup callers that need to distinguish synthetic input.

## Risks
`speakup_fake_down_arrow()` assumes `virt_keyboard` is non-NULL and registered; callers must only inject after successful setup. Disabling local IRQs and preemption makes the section sensitive to any future sleeping call. Only `KEY_DOWN` is advertised, so expanding fake-key support requires updating key bits.

## Test Signals
Test add/remove lifecycle, failure handling for input registration, injected event sequence with input tracing, current-CPU flag behavior during callback handling, and no injection after removal.
