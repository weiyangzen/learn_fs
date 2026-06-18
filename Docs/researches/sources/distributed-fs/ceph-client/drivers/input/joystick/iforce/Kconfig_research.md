# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/Kconfig

Purpose: Kconfig entries for Logitech/Thrustmaster/Guillemot I-Force force-feedback joysticks and wheels. It defines the core driver and separate USB and RS232 transport options.

Important APIs/types/functions: `JOYSTICK_IFORCE` is a tristate core option depending on `INPUT && INPUT_JOYSTICK`. `JOYSTICK_IFORCE_USB` depends on `JOYSTICK_IFORCE && USB`. `JOYSTICK_IFORCE_232` depends on `JOYSTICK_IFORCE && SERIO`.

Control flow: Build configuration selects the core `iforce` module and optionally one or both transport modules. Help text tells users they must select at least one transport, but Kconfig does not enforce this with `select` or dependency logic.

State and persistence: No runtime state; it controls build-time availability.

Dependencies and integration points: Integrates with Linux input joystick Kconfig, USB, SERIO, and documentation references for `inputattach` and force feedback.

Risks: Users can enable the core without a transport and get no usable hardware path. Transport modules depend on the core but are built as independent objects in the Makefile.

Test signals: Kconfig combinations: core only, USB only with core, RS232 only with core, built-in/module mixes, and documentation visibility for RS232 setup.
