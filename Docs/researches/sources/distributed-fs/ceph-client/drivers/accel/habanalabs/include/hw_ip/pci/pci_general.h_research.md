## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/hw_ip/pci/pci_general.h

### Purpose
`pci_general.h` defines common HabanaLabs PCI configuration access registers, status bits, and revision IDs.

### Important APIs, Types, And Functions
Macros identify ELBI PCI config address/data/control/status registers, the write bit, done/error status bits, and a status mask. `enum hl_revision_id` names legal PCI revision IDs `REV_ID_A` through `REV_ID_D`, with zero reserved as invalid.

### Control Flow
No executable code exists. PCI helper code writes config address/data/control, waits for done or error in status, and decodes PCI revision IDs through the enum.

### State, Persistence, And Dependencies
State is PCI configuration space and ELBI access status. The header depends on hardware exposing the config proxy at the fixed offsets.

### Integration Points
It is used by HabanaLabs PCI bring-up, revision-specific workarounds, config-space reads/writes, and diagnostics.

### Risks
Polling the wrong done/error bits can hang config access or miss failures. Treating `REV_ID_INVALID` as a real stepping could apply unsafe workarounds.

### Test Signals
Exercise config reads/writes through the ELBI window, error injection or invalid-address behavior, status mask clearing, and revision-based code paths for every supported stepping.
