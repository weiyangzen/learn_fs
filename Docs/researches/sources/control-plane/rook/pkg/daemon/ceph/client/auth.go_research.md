<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/auth.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/auth.go

Purpose: wraps Ceph CLI auth operations for cephx users: get/create keys, update/read caps, rotate keys, delete users, and list auth entities.

Important APIs/types/functions: `AuthListOutput`, `AuthListEntry`, `AuthGetKey`, `AuthGetOrCreateKey`, `AuthUpdateCaps`, `AuthGetCaps`, `AuthRotate`, `AuthDelete`, `parseAuthKey`, and `AuthList`.

Control flow: each public function builds Ceph command args and executes `NewCephCommand(context, clusterInfo, args).Run()`. Key-get/create parse JSON `key`. `AuthGetCaps` unmarshals `auth get` output as a slice and extracts `mon`, `mds`, `mgr`, and `osd` caps when present. `AuthRotate` handles `EINVAL` specially for Ceph versions that lack `auth rotate`, unmarshals result arrays, warns on multiple results, and returns the first key. `AuthList` unmarshals `auth_dump` entries.

State and persistence behavior: no local persistence; functions mutate or read Ceph monitor auth state. Returned keys are sensitive secrets and logs avoid dumping successful key material, though debug traces can show failed raw auth-list responses.

Dependencies and integration points: depends on `clusterd.Context`, `ClusterInfo`, `NewCephCommand`, JSON decoding, Rook exec exit-status helpers, and syscall errno. Operator code uses these helpers to manage daemon/client credentials.

Risks: several JSON paths use unchecked type assertions and can panic on unexpected Ceph output. `parseAuthKey` assumes a top-level `key` string. Rotate compatibility depends on exit status mapping. Caps extraction ignores cap names outside the four known daemon classes.

Test signals: key parsing, malformed JSON, missing key/caps fields, rotate unsupported EINVAL, multiple/no rotate results, command argument construction, delete/list failures, and sensitive logging behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/auth.go -->
