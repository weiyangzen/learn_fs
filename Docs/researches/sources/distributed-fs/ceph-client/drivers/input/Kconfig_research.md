# sources/distributed-fs/ceph-client/drivers/input/Kconfig

## Purpose

This Kconfig file defines the top-level Linux input subsystem menu, core input options, userland interfaces, helper libraries, KUnit tests, the APM power bridge option, and includes lower-level driver family Kconfig files.

## Important APIs, Types, and Functions

Top-level `config INPUT` enables the generic input layer. Helper/interface options include `INPUT_LEDS`, `INPUT_FF_MEMLESS`, `INPUT_SPARSEKMAP`, `INPUT_MATRIXKMAP`, `INPUT_VIVALDIFMAP`, `INPUT_MOUSEDEV`, `INPUT_MOUSEDEV_PSAUX`, `INPUT_MOUSEDEV_SCREEN_X`, `INPUT_MOUSEDEV_SCREEN_Y`, `INPUT_JOYDEV`, `INPUT_EVDEV`, `INPUT_KUNIT_TEST`, and `INPUT_APMPOWER`.

## Control Flow

There is no runtime control flow. Kconfig shows the input menu, conditionally exposes most options only inside `if INPUT`, sources keyboard, mouse, joystick, tablet, touchscreen, misc, RMI4, serio, and gameport menus, and records selected values into `.config`. The Makefile consumes those symbols to build the input core, handlers, libraries, tests, and subdirectories.

## State and Persistence Behavior

The file persists build configuration state. Screen resolution defaults for mousedev become configuration constants, and tristate settings determine whether components are built-in, modules, or omitted.

## Dependencies and Integration Points

It integrates input core with LED class support, APM emulation, KUnit, userland device interfaces, and hardware-specific input submenus. `INPUT_APMPOWER` depends on `INPUT` and `APM_EMULATION` and maps to `apm-power.o`.

## Risks and Edge Cases

Hidden helper symbols such as `INPUT_VIVALDIFMAP` rely on drivers selecting them. `INPUT` defaults to yes but can be hidden unless `EXPERT` is enabled. Dependency drift between driver source and Kconfig can create invalid build combinations. APM power bridging is expert-only because it can suspend systems directly from input events.

## Test Signals

Build matrix checks should cover built-in and modular input core, evdev/mousedev/joydev variants, helper-library selection by downstream drivers, KUnit enablement, `INPUT_APMPOWER` with and without `APM_EMULATION`, and successful descent into all sourced submenus.
