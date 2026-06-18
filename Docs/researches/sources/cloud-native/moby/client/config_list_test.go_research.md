<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_list_test.go -->
# sources/cloud-native/moby/client/config_list_test.go

Purpose: validates `ConfigList` error handling and filter query encoding.

Important coverage: internal server errors classify correctly; successful cases assert `GET /configs` and inspect `filters` query values, including empty filters and label filters.

Control flow and dependencies: table-driven tests build `Filters`, install mock transports, and decode returned JSON config lists.

State and risks: no persistent state. The tests are a signal for shared `Filters.updateURLValues` integration in config listing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_list_test.go -->
