# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/silergy,sy7636a.yaml

Purpose: Schema for the Silergy SY7636A PMIC used by e-paper displays, combining a regulator, thermal sensor, and GPIO-controlled power-good/enable/VCOM behavior.

Important schema surface and control flow: `compatible = "silergy,sy7636a"`, `reg`, `#thermal-sensor-cells = 0`, `vin-supply`, and `regulators` are required. The binding also defines clock/address cell constants used by its child layout, `epd-pwr-good-gpios`, `enable-gpios`, and `vcom-en-gpios`. The regulator child is constrained to the expected SY7636A output and uses the common regulator schema with additional properties closed.

State, dependencies, and integration: DT state configures the I2C address, input supply, display power GPIOs, thermal sensor provider, and VCOM/regulator constraints for e-paper display stacks. Dependencies include regulator, thermal-sensor, GPIO, and I2C bindings plus the SY7636A MFD/regulator/thermal drivers. Risks include incorrect GPIO polarity delaying panel power sequencing, missing `vin-supply`, and treating the thermal sensor as multi-cell. Test signals are binding validation, thermal zone phandle resolution, regulator registration, and display power sequencing tests with power-good GPIO state.
