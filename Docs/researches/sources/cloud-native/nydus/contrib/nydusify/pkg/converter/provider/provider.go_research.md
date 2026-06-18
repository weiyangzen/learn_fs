# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/provider.go

Purpose: implements the acceleration-service provider interface for Nydus conversion, supporting remote registries and local archive import/export.

Important APIs and flow: `Provider` stores mutex-protected image descriptors, content store, host resolver function, platform matcher, cache settings, chunk size, push retry config, local source/target paths, and plain HTTP flag. `New` creates a content directory and either uses an override store or acceleration-service content. `newDefaultClient` and `newResolver` build Docker resolvers with credentials, TLS skip, plain HTTP, and chunk size. `Pull` imports from local tar or remote-pulls and records the target descriptor. `remotePull` calls ported `fetch`. `SetPushRetryConfig` updates retry settings. `Push` exports to local tar or remote-pushes with retry. `Import` loads an archive and requires exactly one image. `Export`, `Image`, `ContentStore`, `SetContentStore`, `NewRemoteCache`, `WithLocalSource`, and `WithLocalTarget` expose provider operations for converter and chunkdict paths.

State and persistence: creates `<root>/content`, stores blobs/manifests in content store, records image descriptor map, imports/exports tar archives, pushes/pulls remote registry content, and toggles plain HTTP.

Dependencies and integration: central bridge between Harbor acceleration-service converter, containerd remotes/content, cache, Docker auth, local archive modes, and Nydus stream content.

Risks and test signals: `SetContentStore` is not mutex-protected while other methods use the store concurrently. `localPush` opens output without `O_TRUNC`, so overwriting a longer tar can leave trailing bytes. `newDefaultClient` sets `InsecureSkipVerify`; callers must ensure insecure flags are correct. Push retry reuses descriptors but underlying content readers are reopened by `PushContent`.
