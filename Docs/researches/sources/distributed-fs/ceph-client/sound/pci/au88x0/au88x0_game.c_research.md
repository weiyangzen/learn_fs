# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_game.c

## Purpose
Adds optional Linux gameport support for AU88x0 cards when `CONFIG_GAMEPORT` is reachable. It is based on old PCI gameport logic and maps joystick read/trigger/cooked mode operations to Vortex legacy game registers.

## Important APIs, Types, And Functions
Core callbacks are `vortex_game_read`, `vortex_game_trigger`, `vortex_game_cooked_read`, and `vortex_game_open`. Lifecycle helpers are `vortex_gameport_register` and `vortex_gameport_unregister`, with inline `-ENOSYS`/no-op stubs when gameport support is unavailable.

## Control Flow
Registration allocates a `struct gameport`, names it, attaches it to the PCI device, assigns callbacks, stores `vortex_t` as port data, and registers with the input gameport layer. Open switches raw/cooked mode by toggling `CTRL2_GAME_ADCMODE`; cooked reads return buttons from `VORTEX_GAME_LEGACY` and axes from `VORTEX_GAME_AXIS`.

## State And Persistence
State is `vortex->gameport` plus hardware ADC mode bits. It is cleaned by unregistering the port and setting the pointer to NULL. No persistent configuration exists.

## Dependencies And Integration Points
Depends on `linux/gameport.h`, PCI device data, Vortex MMIO macros, and register constants in `au88x0.h`. It integrates with the wider card probe/remove path through the static lifecycle helpers.

## Risks
This is legacy functionality and may be untested on modern kernels/hardware. `vortex_game_open()` returns `-1` instead of a specific errno for unsupported modes. Cooked axis values map `AXIS_RANGE` to `-1`, so hardware interpretation must match the input subsystem expectations.

## Test Signals
When enabled, `/sys`/input should show an AU88x0 gameport, raw and cooked reads should respond to joystick movement/buttons, and unregister should remove the port without use-after-free warnings.
