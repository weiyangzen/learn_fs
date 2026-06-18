## sources/cloud-native/moby/daemon/licensing.go

Purpose: Populates daemon system information with the product license string.

Important API: `(*Daemon).fillLicense(v *system.Info)` sets `v.ProductLicense` to `dockerversion.DefaultProductLicense`.

Control flow and state: The function is a direct assignment with no conditional logic and no daemon state dependency beyond being a method. It mutates the passed `system.Info`.

Dependencies and integration points: Integrates with system info response construction and the `dockerversion` package as the source of the default product license.

Risks: Minimal. Any change to `dockerversion.DefaultProductLicense` flows directly into API responses. A nil `*system.Info` would panic, but callers are expected to pass a valid info object.

Test signals: `licensing_test.go` verifies the assigned field equals `dockerversion.DefaultProductLicense`.
