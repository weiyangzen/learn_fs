# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/hosts.go

Purpose: builds a Harbor acceleration-service `remote.HostFunc` for converter endpoints.

Important APIs and flow: `hosts(opt)` maps source, target, chunk dictionary, and cache refs to their corresponding insecure flags. The returned function always supplies Docker config credentials and returns the insecure flag for the requested ref.

State and persistence: no persistence; reads Docker credentials later through the returned credential function.

Dependencies and integration: used by `provider.New` in `Convert` so registry resolver setup can honor per-reference TLS settings.

Risks and test signals: map lookup defaults unknown refs to `false`, so unregistered refs are treated as secure. Empty string refs can collide in the map when optional fields are unset.
