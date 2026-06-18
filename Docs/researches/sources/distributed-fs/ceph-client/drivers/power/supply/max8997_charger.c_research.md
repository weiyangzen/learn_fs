# sources/distributed-fs/ceph-client/drivers/power/supply/max8997_charger.c

Purpose: implements a MAX8997/MAX8966 battery-control platform subdriver. It exposes basic battery status, presence, and charger-online properties and optionally controls the parent charger regulator in response to MUIC extcon charger-type events.

Important APIs/types/functions: `struct charger_data` stores parent `max8997_dev`, registered battery supply, optional charger regulator, MUIC extcon, notifier, and work item. `max8997_battery_get_property()` reads `STATUS4` bits for full/charging/discharging, detected battery, and DC input. `max8997_battery_extcon_evt_worker()` maps extcon charger types to regulator current limits and enables/disables the regulator. Probe configures EOC and timeout registers from platform data.

Control flow: probe requires parent platform data, programs end-of-charge current and fast-charge timeout fields, allocates state, registers the battery supply, temporarily points the child OF node at the parent to get an optional `charger` regulator, obtains the `max8997-muic` extcon, and if both regulator and extcon are present, registers work/notifier handling. Extcon events schedule work that sets current limit to 450 mA for SDP, 650 mA for other charger classes, or disables the regulator when disconnected.

State and persistence: no cached battery state is kept; status is read from parent I2C registers. EOC/timeout and regulator current/enable state are hardware or regulator-framework state. Work items are devm-managed.

Dependencies and integration: depends on MAX8997 MFD register helpers, platform data, regulator consumer API, extcon MUIC device named `max8997-muic`, devm work helpers, and power-supply core.

Risks: hard-coded extcon lookup by name limits multi-instance support. If the optional regulator is absent, extcon control is skipped but extcon acquisition failures still abort probe. Register update return values are handled for initial config but regulator errors only log in work. Test signals include platform-data validation, EOC/timeout boundary programming, optional regulator absent/defer cases, extcon current-limit transitions, and `STATUS4` bit mapping for full/present/online.
