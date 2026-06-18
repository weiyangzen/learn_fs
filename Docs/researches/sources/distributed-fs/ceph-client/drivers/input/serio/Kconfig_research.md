# sources/distributed-fs/ceph-client/drivers/input/serio/Kconfig

## Purpose

`drivers/input/serio/Kconfig` defines the build-time configuration menu for the Linux serio subsystem and its controller/user drivers. It controls whether the core serio bus and individual PS/2, serial, platform, raw, and userspace serio drivers are built in, built as modules, or excluded.

## Important APIs, Types, and Functions

The main symbol is `SERIO`, a tristate defaulting to `y`. The file also defines architecture gate `ARCH_MIGHT_HAVE_PC_SERIO` and driver symbols such as `SERIO_I8042`, `SERIO_SERPORT`, `SERIO_AMBAKMI`, `SERIO_GSCPS2`, `SERIO_LIBPS2`, `SERIO_RAW`, `SERIO_ALTERA_PS2`, `SERIO_AMS_DELTA`, `SERIO_ARC_PS2`, `SERIO_APBPS2`, `SERIO_GPIO_PS2`, and `USERIO`.

## Control Flow

There is no runtime flow. Kconfig evaluates dependencies and defaults, emits selected symbols into `.config`, and Kbuild uses those symbols in the serio Makefile to include or omit object files. All individual driver choices are nested under `if SERIO`, so disabling `SERIO` removes the submenu.

## State and Persistence Behavior

The file persists build configuration state through `.config`. That state determines the available serio bus core and driver modules. It does not create runtime state.

## Dependencies and Integration Points

The symbols integrate serio with architecture support, TTY, PARPORT, AMBA, SA1111, GSC/HP300, PCI, SGI, OF, HAS_IOMEM, Hyper-V, GPIOLIB, and platform-specific machine symbols. Module names in help text match Makefile object targets.

## Risks and Edge Cases

Dependency drift can leave a driver visible without required infrastructure or hidden when compile-test coverage would be useful. Some defaults are architecture-specific and can surprise minimal configurations. Help text references older documentation paths and platform names, so user guidance can lag code movement.

## Test Signals

Build matrix checks should cover `SERIO=y/m/n`, each requested driver symbol as built-in and module where dependencies allow, dependency-disabled visibility, randconfig coverage, and Makefile object emission matching the configured symbols.
