# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/table.h

## Purpose
Declares all generated RTL8812AE/RTL8821AE hardware table symbols consumed by PHY initialization and regulatory power parsing.

## Important APIs, Types, And Functions
The header declares length/data pairs for PHY register arrays, PHY power-group arrays, RF radio arrays, MAC register arrays, AGC tables, and TX power limit string arrays. It exposes both RTL8812AE and RTL8821AE variants, with RTL8812AE having Radio A and B arrays and RTL8821AE having Radio A data.

## Control Flow
No executable control flow is present. Inclusion allows table consumers to select the correct array and length according to hardware type and configuration.

## State And Persistence
No local state. The declared globals are defined in `table.c` and persist for the lifetime of the loaded module.

## Dependencies And Integration Points
Includes `<linux/types.h>` for `u32`. Integrated directly with `rtl8821ae/phy.c` table parser code and indirectly with RF/power initialization.

## Risks And Edge Cases
The declarations are non-`const` for the register arrays, matching their definitions but weakening compile-time protection. Any mismatch between declaration type and definition, especially for `const char *` TX power limit arrays, would be caught at build time but can break consumers if not updated with parser changes.

## Test Signals
Compile coverage is the direct signal. Runtime PHY table loading for both supported chip IDs validates that every declared symbol resolves and uses the intended length.
