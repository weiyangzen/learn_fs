# sources/cloud-native/nydus/contrib/nydusify/pkg/provider/remote.go

Purpose: constructs default registry remotes backed by containerd Docker resolver/auth clients.

Important APIs/functions: `newDefaultClient`, `withCredentialFunc`, `withRemote`, `DefaultRemote`, and `DefaultRemoteWithAuth`.

Control flow: `newDefaultClient` configures a short-lived HTTP transport with optional TLS skip verify, disabled keepalives, and HTTP/2 disabled via `TLSNextProto`. `withRemote` creates a resolver function that configures Docker registries with authorizer, client, and plain HTTP toggled by retry state. `DefaultRemote` reads Docker config credentials, mapping Docker Hub's resolver host to `https://index.docker.io/v1/`. `DefaultRemoteWithAuth` decodes base64 `username:password` and supplies fixed credentials.

State and persistence: no durable state; remotes hold reference and resolver factory. Docker config is read when credential callback is invoked.

Dependencies and integration points: containerd docker resolver, Docker CLI config loading, HTTP/TLS, base64 auth, and the local `remote.Remote` wrapper.

Risks and test signals: `InsecureSkipVerify` is used for insecure mode. Base64 auth cannot contain additional colons. Plain HTTP is controlled per resolver request from `remote.Remote` state.
