# sources/distributed-fs/ceph-client/net/atm/protocols.h

## Purpose
`protocols.h` is the private declaration header for raw ATM adaptation layer initializers. It lets the common VCC connection code install the correct push/pop/send handlers for AAL0, AAL3/4, or AAL5.

## Important APIs
- `atm_init_aal0(struct atm_vcc *vcc)`: initializes raw AAL0 behavior, including the restricted send wrapper.
- `atm_init_aal34(struct atm_vcc *vcc)`: initializes raw AAL3/4 transport.
- `atm_init_aal5(struct atm_vcc *vcc)`: initializes raw AAL5 transport and is exported by `raw.c`.

## Control Flow and State
The header owns no state. Callers select one initializer after QoS/AAL negotiation; each initializer mutates the passed `atm_vcc` callback pointers.

## Dependencies and Integration
The declarations depend on `struct atm_vcc` from ATM core headers. Implementations live in `raw.c`; consumers are the common ATM VCC setup paths.

## Risks and Test Signals
The risk is callback contract drift: these functions must install complete and compatible VCC data-plane callbacks. Test signals include PVC/SVC connections using AAL0, AAL3/4, and AAL5, correct behavior with devices that provide `send_bh`, and successful builds when only raw AAL5 is used externally.
