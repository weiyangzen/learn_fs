# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-pstop.c

## Purpose
`coresight-cfg-pstop.c` defines an ETMv4 preloaded configuration named `panicstop`. It programs ETM resources to generate an external trigger when execution reaches the kernel `panic` symbol, allowing trace infrastructure to stop or react around panic handling.

## Important APIs, Types, And Functions
`gen_etrig_params` contains one parameter, `address`, defaulted to `(u64)panic`. `gen_etrig_regs` programs an ETMv4 resource selector, a 64-bit address comparator driven by the parameter, comparator attributes, and `TRCEVENTCTL0R` to route comparator output to driver external output 0. `gen_etrig_etm4x` describes the `gen_etrig` feature. `pstop_etm4x` describes the `panicstop` configuration and references `gen_etrig`.

## Control Flow
Like the AFDO descriptor file, this file is declarative. At syscfg preload time, `coresight-cfg-preload.c` supplies the feature/config descriptors to the loader. At activation time, generic configuration code updates ETMv4 driver register storage so the hardware is programmed when the ETM source is enabled.

## State And Persistence
Descriptor state is static. The default panic address is captured at build/runtime link time through the `panic` symbol. Per-device runtime copies of register descriptors and parameters are owned by the generic config subsystem after load.

## Dependencies And Integration Points
The file depends on ETMv4 register definitions and `coresight-config.h`. It also depends on the global kernel `panic` symbol being valid as a match address. It integrates with ETMv4 external trigger routing and the preloaded syscfg path.

## Risks
Address matching for `panic` is architecture, KASLR, and symbol-reachability sensitive. The comparator attribute value `0xf00` and event control value must match ETMv4 expectations; mistakes can either never trigger or trigger on the wrong context. The configuration has no presets and one parameter, so user updates to the address should be validated by the generic config interface.

## Test Signals
Tests should verify `panicstop` appears as a preloaded configuration, loads into ETMv4 devices, programs a 64-bit address comparator, and can be activated without disturbing normal ETM programming. Hardware validation would use a controlled function address rather than forcing a real panic.
