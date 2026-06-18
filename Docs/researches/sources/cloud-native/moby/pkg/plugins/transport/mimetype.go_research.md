<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/mimetype.go -->
# sources/cloud-native/moby/pkg/plugins/transport/mimetype.go

Purpose: defines the plugin protocol version MIME type sent in plugin client `Accept` headers. `VersionMimetype` is aliased by the parent `plugins` package. State and control flow are absent. Dependencies are none. Risks are compatibility-sensitive: changing the string can break legacy plugin negotiation. Test signal is through transport and client tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/mimetype.go -->
