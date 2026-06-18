<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/benchmark.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/benchmark.h

## Purpose
Declares the benchmark entry point and defines the synthetic load macro `ROUNDS(x)`. The macro performs `x * 1000` iterations of `pow`, `sqrt`, integer xor, and `atan2` expressions to burn CPU time.

## Important APIs, Types, And Functions
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## Control Flow
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## State And Persistence
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## Dependencies And Integration Points
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## Risks And Edge Cases
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.

## Test Signals
Control flow is macro expansion inside calibration and benchmark loops; there is no persistent state. Dependencies are `math.h` availability in includers and `struct config` from `parse.h` or equivalent prior declarations. Risks include multiple evaluation of `x`, integer overflow in `x * 1000`, dependency on optimizer behavior, and expensive libm calls skewing benchmark portability. Test signals are successful link with `-lm`, calibration stability, and compiler warning checks under different optimization levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/benchmark.h -->
