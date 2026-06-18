# sources/distributed-fs/ceph/src/rgw/rgw_http_client_curl.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header declares `rgw::curl::fe_map_t`, `setup_curl()`, and `cleanup_curl()`. It is the narrow lifecycle API for curl/OpenSSL initialization and saved-handle cleanup, with optional access to RGW frontend configuration. All state is global implementation state. It depends on Boost optional and `rgw_frontend.h`, and must be coordinated with HTTP manager/request lifetimes. Tests should compile and run setup with no frontend map and with Beast SSL frontend config, then verify cleanup happens after active HTTP use has stopped.
