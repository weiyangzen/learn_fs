
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/usb.c

## Purpose
Small QE helper that selects the QE USB clock source and optionally programs a BRG clock rate. It exports `qe_usb_clock_set()` for USB-related QE drivers.

## Important APIs, Types, and Functions
- `qe_usb_clock_set(enum qe_clock clk, int rate)` maps supported QE clocks/BRGs to `QE_CMXGCR_USBCS_*` values, calls `qe_setbrg()` for BRG clocks, and updates `cmxgcr` under `cmxgcr_lock`.

## Control Flow
The function switches on the requested clock, rejects unsupported values with `-EINVAL`, configures BRG rate when relevant, takes `cmxgcr_lock`, replaces the USB clock select field, releases the lock, and returns success.

## State and Persistence
Only global QE mux register state is changed. There is no private state.

## Dependencies and Integration Points
Depends on global QE IMMR mapping, QE clock definitions, `qe_clock_is_brg()`, `qe_setbrg()`, and `cmxgcr_lock`. It is intended for QE USB controller setup.

## Risks
Unsupported clock values are rejected, but invalid rates for BRGs depend on `qe_setbrg()` behavior. The function assumes QE global registers are already mapped.

## Test Signals
Test every supported clock enum, unsupported enum rejection, BRG rate programming, and cmxgcr field preservation outside `QE_CMXGCR_USBCS`.
