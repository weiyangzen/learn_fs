# sources/distributed-fs/ceph-client/include/dt-bindings/usb/pd.h

Source read summary: 505 lines, 17678 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/usb/pd.h` defines the USB Type-C Power Delivery wire-level constants and helper macros used by device trees and drivers to encode PDOs, RDOs, VDOs, SVDMs, cable/plug capabilities, power roles, data roles, and alternate-mode discovery fields.

Important APIs, types, and functions: The file exports 196 visible constants or packing macros; representative names are `PDO_TYPE_FIXED`, `PDO_TYPE_BATT`, `PDO_TYPE_VAR`, `PDO_TYPE_APDO`, `PDO_TYPE_SHIFT`, `PDO_TYPE_MASK`, `PDO_VOLT_MASK`, `PDO_CURR_MASK`, `PDO_PWR_MASK`, `PDO_FIXED_DUAL_ROLE`, `PDO_FIXED_SUSPEND`, `PDO_FIXED_HIGHER_CAP`, `PDO_FIXED_EXTPOWER`, `PDO_FIXED_USB_COMM`, `PDO_FIXED_DATA_SWAP`, `PDO_FIXED_VOLT_SHIFT` and 180 more. Function-like helpers include `PDO_TYPE`, `PDO_FIXED_VOLT`, `PDO_FIXED_CURR`, `PDO_FIXED`, `PDO_BATT_MIN_VOLT`, `PDO_BATT_MAX_VOLT`, `PDO_BATT_MAX_POWER`, `PDO_BATT`, `PDO_VAR_MIN_VOLT`, `PDO_VAR_MAX_VOLT`, `PDO_VAR_MAX_CURR`, `PDO_VAR`, `PDO_APDO_TYPE`, `PDO_PPS_APDO_MIN_VOLT`, `PDO_PPS_APDO_MAX_VOLT`, `PDO_PPS_APDO_MAX_CURR` and 18 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: `PDO_*`, `RDO_*`, `VDO_*`, and `SVDM_*` helpers pack policy-engine choices into protocol bitfields; USB-C controller drivers and board descriptions consume the same constants so advertised source/sink capabilities match the kernel's PD parser.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bit shift, mask, and unit mistakes can advertise unsafe voltage/current combinations or select the wrong alternate mode. The macros intentionally do not validate electrical feasibility, so callers must enforce PD specification constraints.

Test signals: Build DTS users, decode generated PDO/RDO/VDO values against the USB PD spec, run Type-C negotiation tests for fixed, battery, variable, PPS, and AVS supplies, and cover role-swap and alternate-mode discovery messages.
