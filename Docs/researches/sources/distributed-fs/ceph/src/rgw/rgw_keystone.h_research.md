# sources/distributed-fs/ceph/src/rgw/rgw_keystone.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header declares Keystone config abstraction, HTTP token transceiver, token envelope model, singleton LRU token cache, and admin/Barbican token request serializers. `TokenEnvelope` models token/project/domain/user/roles/application credentials and exposes parse/expiry/role helpers; `TokenCache` manages normal/service/admin/Barbican token entries with LRU state. It integrates with RGW Keystone auth engines and Keystone scope logging. Risks include singleton/global-context coupling, cached token expiry requirements, missing `X-Subject-Token` returning an empty static string, and caller lifetime around cache singletons. Tests should use mock config, token JSON decode, cache add/find/invalidate, admin/Barbican shortcuts, and header capture.
