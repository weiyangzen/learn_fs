# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-interrupt-rsl.c

## Purpose
Enables ASX and GMX error reporting for RSL interrupt blocks, delegating GMX RX masks to generated helpers.

## Important APIs, Types, And Functions
Functions are `__cvmx_interrupt_asxx_enable()` and `__cvmx_interrupt_gmxx_enable()`. They write `CVMX_ASXX_INT_EN`, read `CVMX_GMXX_INF_MODE`, write `CVMX_GMXX_TX_INT_EN`, and call `__cvmx_interrupt_gmxx_rxx_int_en_enable()`.

## Control Flow
ASX enable chooses a three- or four-port mask and enables TX push/pop plus overflow. GMX enable determines active error-reporting ports from model and mode, enables TX underflow/NXA bits, and enables RX masks per active port.

## State, Persistence, And Dependencies
State is interrupt-enable CSR configuration. GMX mode must be configured before this runs.

## Integration Points
Mode-specific helper enable paths call these functions after port hardware setup.

## Risks
Wrong port count causes missed or spurious interrupts. SPI on CN38XX/CN58XX reports GMX errors only through port 0.

## Test Signals
Check ASX/GMX interrupts under injected faults, correct port counts per mode, and no interrupts for disabled interfaces.
